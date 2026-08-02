function Dashboard() {
  return (
    <div>

      <h2 className="mb-6 text-3xl font-bold">
        Dashboard
      </h2>

      <div className="grid grid-cols-5 gap-5">

        <Card title="Organizations" value="1" />

        <Card title="Repositories" value="0" />

        <Card title="Documents" value="0" />

        <Card title="Knowledge Nodes" value="0" />

        <Card title="AI Queries" value="0" />

      </div>

    </div>
  );
}

function Card(
    {
        title,
        value
    }:
    {
        title:string;
        value:string;
    }
){

    return(

        <div className="rounded-xl bg-white p-6 shadow">

            <p className="text-slate-500">
                {title}
            </p>

            <h2 className="mt-3 text-3xl font-bold">
                {value}
            </h2>

        </div>

    );

}

export default Dashboard;